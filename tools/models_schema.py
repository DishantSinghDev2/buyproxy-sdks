"""Single source of truth for the response models of the dynamic/enterprise SDKs (PHP, Ruby, Java, C#).
Types: str int float bool, ?T nullable, list:T list, Name = another model.
Field names are the API's camelCase JSON keys."""

PLAN_FIELDS = [
    ("id", "str"), ("productId", "str"), ("productKey", "?str"), ("name", "str"), ("label", "?str"),
    ("dataGbRemaining", "float"), ("dataGbTotal", "float"), ("expiresAt", "?str"), ("createdAt", "str"),
    ("generate", "?GenerateCapabilities"),
]

MODELS = {
    "Product": ("A product in the catalog.", [("productKey", "str"), ("productId", "str"), ("name", "str"), ("description", "str"), ("minGb", "int"), ("pricePerGbCents", "?int"), ("currency", "str")]),
    "VolumeBonus": ("Top-ups of thresholdGb or more get floor(gb × rate) extra GB free.", [("thresholdGb", "int"), ("rate", "float")]),
    "PlanPrice": ("A subscription plan's price.", [("plan", "str"), ("monthlyPriceCents", "int"), ("includedGb", "float")]),
    "Catalog": ("The public product catalog with live prices.", [("products", "list:Product"), ("volumeBonus", "VolumeBonus"), ("plans", "list:PlanPrice")]),
    "Account": ("The account behind the API key.", [("email", "str"), ("name", "str"), ("plan", "str"), ("planExpiresAt", "?str"), ("balanceGb", "float"), ("createdAt", "str")]),
    "Balance": ("Spendable bandwidth on one product.", [("productKey", "?str"), ("productId", "str"), ("planId", "?str"), ("activeGb", "float"), ("pendingGb", "float"), ("totalGb", "float"), ("expiresAt", "?str")]),
    "Targeting": ("Which targeting fields a plan supports.", [("country", "bool"), ("state", "bool"), ("city", "bool"), ("isp", "bool")]),
    "GenerateCapabilities": ("What a plan's generate call accepts.", [("maxCount", "int"), ("maxStickyMinutes", "int"), ("protocols", "list:str"), ("targeting", "Targeting")]),
    "Plan": ("Bandwidth you hold on one product.", PLAN_FIELDS),
    "CardCheckout": ("A Stripe checkout to open in a browser.", [("payUrl", "str"), ("transactionId", "?str")]),
    "CryptoCheckout": ("A crypto invoice to open in a browser.", [("url", "str"), ("transactionId", "str")]),
    "Transaction": ("One payment.", [("id", "str"), ("kind", "str"), ("status", "str"), ("paymentMethod", "str"), ("interval", "?str"), ("amountCents", "int"), ("currency", "str"), ("gb", "?float"), ("productKey", "?str"), ("plan", "?str"), ("resellerPool", "bool"), ("createdAt", "str")]),
    "PoolEntry": ("Unallocated reseller bandwidth on one product.", [("productKey", "str"), ("productId", "str"), ("label", "str"), ("gb", "float")]),
    "ResellerSummary": ("Reseller account summary.", [("email", "str"), ("customerCount", "int"), ("activeCustomerCount", "int"), ("pool", "list:PoolEntry")]),
    "Customer": ("A reseller sub-account.", [("username", "str"), ("label", "str"), ("status", "str"), ("createdAt", "str")]),
    "PendingAllocation": ("GB allocated but still being added to a plan.", [("productId", "str"), ("productKey", "?str"), ("gb", "float")]),
    "CustomerPlan": ("A plan plus the customer's remaining GB.", PLAN_FIELDS + [("remainingGb", "float")]),
    "CustomerDetail": ("A customer with their plans.", [("username", "str"), ("label", "str"), ("status", "str"), ("createdAt", "str"), ("plans", "list:CustomerPlan"), ("pending", "list:PendingAllocation")]),
    "UsagePlan": ("Consumption on one plan.", [("id", "str"), ("productId", "str"), ("productKey", "?str"), ("remainingGb", "float"), ("totalGb", "float"), ("usedGb", "float"), ("expiresAt", "?str")]),
    "CustomerUsage": ("A snapshot of a customer's consumption.", [("plans", "list:UsagePlan"), ("pending", "list:PendingAllocation")]),
    "Allocation": ("The result of an allocation.", [("productKey", "str"), ("productId", "str"), ("gb", "int"), ("alreadyApplied", "bool"), ("poolRemainingGb", "float")]),
    "SignupResult": ("The result of signup.", [("ok", "bool"), ("cooldownSeconds", "?int")]),
    "VerifiedUser": ("The verified user.", [("email", "str"), ("name", "str")]),
    "VerifyResult": ("The result of OTP verification.", [("ok", "bool"), ("isNew", "bool"), ("user", "VerifiedUser")]),
}

def parse(t):
    nullable = t.startswith("?")
    t = t.lstrip("?")
    if t.startswith("list:"):
        return nullable, "list", t[5:]
    return nullable, "scalar" if t in ("str", "int", "float", "bool") else "model", t

def snake(name):
    out = ""
    for ch in name:
        out += ("_" + ch.lower()) if ch.isupper() else ch
    return out

def pascal(name):
    return name[0].upper() + name[1:]

SCALARS = ("str", "int", "float", "bool")
