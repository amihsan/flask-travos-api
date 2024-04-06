import logging
from flask import jsonify
from final_result import  final_travos_result



def perform_evaluation(scenario_details):
    try:

        # Convert ObjectId to string for JSON serialization
        scenario_details['_id'] = str(scenario_details['_id'])

        # Perform your evaluation logic here
        observations = scenario_details['observations']
        result = []

        # Perform your calculations for each observation
        for i, obs in enumerate(observations, start=1):
            sender = obs['sender']
            recipient = obs['recipient']

            output = final_travos_result(sender, recipient, scenario_details)

            # Use the correct observation index in the dynamic key
            observation_key = f"observation({i})"
            
            result.append({
                observation_key: obs['message'],
                'final_trust_score': output[0],
                'final_trust_outcome': output[1],
                'previous_history': output[2],
                'sender': sender,
                'receiver': recipient
            })

        
        # print(result)

        return result


    except Exception as e:
        # Log any exceptions that occur during evaluation
        logging.error("Error in perform_evaluation: %s", str(e))
        # You may choose to raise the exception or handle it gracefully
        raise


