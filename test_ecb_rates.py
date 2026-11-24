from ecb_rates import get_historical_conversion_rate

rate = get_historical_conversion_rate("GBP", "2026-11-23")

print("GBP to USD:", rate)

usd_rate = get_historical_conversion_rate("USD", "2026-11-23")

print("USD to USD:", usd_rate)
