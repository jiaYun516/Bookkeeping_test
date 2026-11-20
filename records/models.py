from django.db import models

# 分類
class Category(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, blank=True, null=True) # 方便前端顯示小圖示
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

# 帳戶：管理錢包、台新、中信、外幣等
class Account(models.Model):
    name = models.CharField(max_length=50)
    currency = models.CharField(max_length=10, default='TWD') # 幣別
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# 聯絡人：你自己、或是代購的小明、小美
class Contact(models.Model):
    name = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# 交易主單
class Transaction(models.Model):
    class TypeChoices(models.TextChoices):
        EXPENSE = 'expense', '支出'
        INCOME = 'income', '收入'
        TRANSFER = 'transfer', '轉帳'

    transaction_type = models.CharField(
        max_length=10,
        choices=TypeChoices.choices,
        default=TypeChoices.EXPENSE
    )
    
    # 來源帳戶 (支出、轉帳時扣款的帳戶；或是收入時入帳的帳戶)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transactions')
    
    # 目標帳戶 (只有「轉帳」時會用到)
    to_account = models.ForeignKey(
        Account, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='incoming_transfers',
        help_text="僅在轉帳時填寫"
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"[{self.get_transaction_type_display()}] {self.date.strftime('%Y-%m-%d')} | ${self.total_amount}"

# 交易明細：處理拆帳與標籤
class TransactionItem(models.Model):
    # 定義狀態選項
    class StatusChoices(models.TextChoices):
        NONE = 'none', '無'
        PRE_ORDER = 'pre_order', '非現貨'
        DELIVERED = 'delivered', '已交貨'

    transaction = models.ForeignKey(Transaction, related_name='items', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    selling_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # FK 指向分類
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    
    # 寫死的狀態選擇
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.NONE
    )
    
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT)
    tag = models.CharField(max_length=50, blank=True, help_text="例如：代購商品名稱或周邊名稱")

    def __str__(self):
        return f"[{self.category.name}] {self.tag} - ${self.amount} ({self.get_status_display()})"
        