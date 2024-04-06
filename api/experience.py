def experience(sender, recipient, history):
    # determine no of successful (m) and no of unsuccessful (n) interactions from history tuple
    m = history[0]
    n = history[1]

    # shape parameter for pdf
    alpha = m + 1
    beta = n + 1

    direct_trust = alpha / (alpha + beta)
    print(direct_trust)

    return direct_trust
