# Money Problems · q09-03 · A tiny Money type
# Whole minor units plus a currency. Rounding only happens when you ask.
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN

MINOR_DIGITS = {"USD": 2, "JPY": 0, "KWD": 3}

@dataclass(frozen=True)
class Money:
    minor: int
    currency: str

    @classmethod
    def of(cls, text, currency):
        scaled = Decimal(text).scaleb(MINOR_DIGITS[currency])
        if scaled != scaled.to_integral_value():
            raise ValueError(f"{text} has too many decimals for {currency}")
        return cls(int(scaled), currency)

    def __add__(self, other):
        if other.currency != self.currency:
            raise ValueError(f"can't add {other.currency} to {self.currency}")
        return Money(self.minor + other.minor, self.currency)

    def times(self, rate, rounding=ROUND_HALF_EVEN):
        exact = self.minor * Decimal(rate)
        return Money(int(exact.to_integral_value(rounding)), self.currency)

    def __str__(self):
        digits = MINOR_DIGITS[self.currency]
        return f"{self.currency} {Decimal(self.minor).scaleb(-digits)}"

print(Money.of("19.99", "USD") + Money.of("0.01", "USD"))
print(Money.of("1500", "JPY"), "|", Money.of("1.25", "KWD"))
print(Money.of("19.99", "USD").times("0.0825", ROUND_HALF_EVEN))
for bad in [lambda: Money.of("1.005", "USD"),
            lambda: Money.of("5", "USD") + Money.of("5", "JPY")]:
    try:
        bad()
    except ValueError as error:
        print("ValueError:", error)
