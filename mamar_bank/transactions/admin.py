from django.contrib import admin

# from transactions.models import Transaction
from .models import Transaction, BankCondition
@admin.register(Transaction,)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'balance_after_transaction', 'transaction_type', 'loan_approve']
    
    def save_model(self, request, obj, form, change):
        obj.account.balance += obj.amount
        obj.balance_after_transaction = obj.account.balance
        obj.account.save()
        super().save_model(request, obj, form, change)

# Admin for the Bank model
@admin.register(BankCondition)
class BankAdmin(admin.ModelAdmin):
    list_display = ['is_bankrupt']

    # If you want to customize the save behavior of the Bank model:
    def save_model(self, request, obj, form, change):
        # Custom logic for saving the Bank model if needed
        super().save_model(request, obj, form, change)

