def look_for_opinions(sender, recipient, scenario_details):

    # store the list of available opinion provider agent
    opinion_provider_agent = [provider_agent for provider_agent in scenario_details["users"] if provider_agent != sender and provider_agent != recipient]

    opinion_outcome = []

    # Iterate through each opinion provider agent
    for provider_agent in opinion_provider_agent:
        # Get the data tuple from history
        data_tuple = scenario_details["history"][provider_agent][sender]["data"]
        opinion_outcome.append(data_tuple)


    # Calculate M(successful) and N(unsuccessful) (from opinion_outcome)
    M = sum(value[0] for opinion in opinion_outcome for value in [opinion])
    N = sum(value[1] for opinion in opinion_outcome for value in [opinion])

    # Calculate shape parameter alpha and beta
    alpha = M + 1
    beta = N + 1

    # Calculate new opinion trust  value for other_agent
    opinion_trust_value = alpha / (alpha + beta)

    print(f"opinion provider : {opinion_provider_agent}")
    print(f"Opinion tuple:{opinion_outcome}")
    print(f"Shape parameter for opinion: ({alpha}, {beta})")
    print(f"The opinion trust value for {recipient} is: {opinion_trust_value}")



    return opinion_trust_value

    
