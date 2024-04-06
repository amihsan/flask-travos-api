from confidence import calculate_confidence_value
from opinion import look_for_opinions
from experience import experience


def final_travos_result(sender, recipient, scenario_details):

    # Predefined threshold values for comparison in travos. (may change)
    confidence_threshold = 0.95
    cooperation_threshold = 0.50

    history = scenario_details["history"][recipient][sender]["data"]

    # Calculate experience value. returns tuple
    experience_value = float(experience(sender, recipient, history))

    # Calculate confidence value
    confidence_value = float(calculate_confidence_value(experience_value, history))

    

    # Decision-making process (comparison)
    if confidence_value > confidence_threshold:
        print(
            f"Opinion not needed as confidence value '{confidence_value}' > confidence threshold "
            f" '{confidence_threshold}'")
        print(f"Experience value is Final trust score: {experience_value}")

        final_trust_value = experience_value

        if experience_value > cooperation_threshold:
            print('Trustworthy')
            final_outcome = str((history[0] + 1, history[1]))
        
           
        else:
            print('Not Trustworthy')
            final_outcome = str((history[0], history[1] + 1))
           
      

    if confidence_value < confidence_threshold:

        # Calculate Opinion value
        opinion_value = float(look_for_opinions(sender, recipient, scenario_details))

        final_trust_value = opinion_value

        print(
            f"Opinion needed as confidence value '{confidence_value}' < confidence threshold '{confidence_threshold}'")
        print(f"Opinion value is Final trust score: {opinion_value}")

        if opinion_value > cooperation_threshold and opinion_value >= experience_value:
            print('Trustworthy')
            final_outcome = str((history[0] + 1, history[1]))
          
           
          
        else:
            print('Not Trustworthy')
            final_outcome = str((history[0], history[1] + 1))
         
    return final_trust_value, final_outcome, str(tuple(history)), sender, recipient
