from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from scipy.stats import beta
from scipy.integrate import quad

app = Flask(__name__)
CORS(app)


# Load environment variables from .env file
load_dotenv()

# Retrieve MongoDB connection details from environment variables
mongodb_uri = os.getenv('MONGODB_URI')
database_name = os.getenv('DATABASE_NAME')


# Connect to MongoDB
client = MongoClient(mongodb_uri)
db = client[database_name]

# Default Route: Hello From Ihsan
@app.route('/')
def index(): 
    try:
        return '<b><big>Hello From Travos lab</big></b>'
    except Exception as e:
        error_message = f'An error occurred: {str(e)}'
        return error_message
    
@app.route("/api")
def index_again():
    return render_template('index.html')

    
# Route 1: Get All Scenarios List
@app.route('/api/getAllScenarios')
def get_all_scenarios():
    try:
        collections = db.list_collection_names()
        return collections
    
    except Exception as e:
        return handle_error('get_all_scenarios', f'An error occurred: {str(e)}')
    
# Route 2: Get Scenario Details
@app.route('/api/getScenarioDetails/<int:scenario_number>')
def get_scenario_details(scenario_number):
    try:
        scenario_collection = db[f'scenario_{scenario_number}']
        scenario_details = scenario_collection.find_one()

        if scenario_details is None:
            return jsonify({'error': f'Scenario {scenario_number} not found'}), 404

        # Convert ObjectId to string for JSON serialization
        scenario_details['_id'] = str(scenario_details['_id'])

        return jsonify(scenario_details)
    
    except Exception as e:
        return handle_error('get_scenario_details', f'An error occurred: {str(e)}')

# Route 3: Start Evaluation
@app.route('/api/startEvaluation', methods=['POST'])
def start_evaluation():
    try:
        selected_scenario = request.json.get('scenario')

        scenario_collection = db[f'scenario_{selected_scenario}']
        scenario_details = scenario_collection.find_one()

        if scenario_details is None:
            return jsonify({'error': f'Selected scenario {selected_scenario} not found'}), 404

        evaluation_results = perform_evaluation(scenario_details)

        return jsonify({'message': f'Evaluation started for scenario {selected_scenario}', 'results': evaluation_results})
    
    except Exception as e:
        return handle_error('start_evaluation', f'An error occurred: {str(e)}')

def handle_error(route_name, error_message, status_code=500):
    # Simplified error handling function
    return jsonify({'error': error_message}), status_code

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





if __name__ == '__main__':
    app.run(debug=True)