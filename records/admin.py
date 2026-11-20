from django.contrib import admin
from .models import Category, Account, Contact, Transaction, TransactionItem

class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 1

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'account', 'total_amount', 'note')
    inlines = [TransactionItemInline] # 把明細內嵌進來

# 其他簡單的註冊
admin.site.register(Category)
admin.site.register(Account)
admin.site.register(Contact)
