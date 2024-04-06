from scipy.stats import beta
from scipy.integrate import quad


def calculate_confidence_value(experience_value, history):

    # Predefined value for travos. may change (such as 0.1)
    error_threshold = 0.2


    # Confidence value
    confidence_value = beta_integral(experience_value - error_threshold, experience_value + error_threshold, history[0] + 1, history[1] + 1) / beta_integral(0, 1, history[0] + 1, history[1] + 1)
    print(f"Confidence : {confidence_value}")
    return confidence_value


# integral function for travos confidence value calculation
def beta_integral(lower_limit, upper_limit, alpha, beta_):
    dist = beta(alpha, beta_)
    pdf = lambda x: dist.pdf(x)
    integral, _ = quad(pdf, lower_limit, upper_limit)
    return integral
