from django import forms
from .models import Transaction
from accounts.models import UserBankAccount
from .constants import TRANSACTION_TYPE

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type'
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account') # account value ke pop kore anlam
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True # ei field disable thakbe
        self.fields['transaction_type'].widget = forms.HiddenInput() # user er theke hide kora thakbe

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositForm(TransactionForm):
    def clean_amount(self): # amount field ke filter korbo
        min_deposit_amount = 100
        amount = self.cleaned_data.get('amount') # user er fill up kora form theke amra amount field er value ke niye aslam, 50
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )

        return amount


class WithdrawForm(TransactionForm):

    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        balance = account.balance # 1000
        amount = self.cleaned_data.get('amount')
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} $'
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw_amount} $'
            )

        if amount > balance: # amount = 5000, tar balance ache 200
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You can not withdraw more than your account balance'
            )

        return amount
    
class TransferForm(forms.ModelForm):
    recipient_account = forms.ModelChoiceField(
        queryset=UserBankAccount.objects.all(),
        label="Recipient Account",
        required=True,
    )

    class Meta:
        model = Transaction
        fields = ['amount', 'recipient_account']  # Include recipient_account

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')  # Current user's account passed during form creation
        super().__init__(*args, **kwargs)
        recipient_queryset = UserBankAccount.objects.exclude(id=self.account.id)
        self.fields['recipient_account'].queryset = recipient_queryset

    def clean_recipient_account(self):
        recipient_account = self.cleaned_data.get('recipient_account')
        if recipient_account == self.account:
            raise forms.ValidationError("You cannot transfer money to your own account.")
        return recipient_account

    def clean_amount(self):
        account = self.account
        min_transfer_amount = 500
        max_transfer_amount = 20000
        balance = account.balance  # Sender's current balance
        amount = self.cleaned_data.get('amount')

        if amount < min_transfer_amount:
            raise forms.ValidationError(
                f'You can transfer at least {min_transfer_amount} $'
            )
        if amount > max_transfer_amount:
            raise forms.ValidationError(
                f'You can transfer at most {max_transfer_amount} $'
            )
        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You cannot transfer more than your account balance.'
            )
        return amount

    def save(self, commit=True):
        # The logic will be handled in the view
        return super().save(commit=False)

class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        return amount
    

