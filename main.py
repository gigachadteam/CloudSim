import simpy
import random
import statistics

# Global vars
wait_times = []
WEBSITE_SIZE = 10
waited = 0

class CloudProvider:
    def __init__(self, env, num_of_nodes, num_of_helpdesks):
        self.env = env
        self.node = simpy.Resource(env, num_of_nodes)
        self.helpdesk = simpy.Resource(env, num_of_helpdesks)
    
    def utilize_web_service(self, user, service_time):
        yield self.env.timeout(service_time) 
    def utilize_bucket_service(self, user):
        yield self.env.timeout(random.randint(2,4))

    def call_help(self, user, service_time):
        yield self.env.timeout(random.randint(2,5)) # Random time to process the call

def open_website(env, user, CloudProvider, internet_speed):
    service_time = random.randint(1,3) + WEBSITE_SIZE/internet_speed # Random time to browse + the speed of loading
    arrival_time = env.now
    # Request a node for web
    with CloudProvider.node.request() as request:
        yield request
        yield env.process(CloudProvider.utilize_web_service(user, service_time))
    wait_times.append(env.now - arrival_time - service_time)

def call_helpdesk(env, user, CloudProvider):
    service_time = random.randint(2,5)
    arrival_time = env.now
    # Request for help desk
    with CloudProvider.helpdesk.request() as request:
            yield request
            yield env.process(CloudProvider.call_help(user, service_time))
    wait_times.append(env.now - arrival_time - service_time)
        
def run_cloud(env, num_of_nodes, num_of_helpdesks):
    # Initlize the cloud
    cloud = CloudProvider(env, num_of_nodes, num_of_helpdesks)
    
    user = 0
    while True:
        waited = 0
        user = user + 1 # Increment user
        internet_speed = random.randint(1, 10) # Give internet speed
        
        # The customer arrived right now
        arrival_time = env.now;
        print(f"user {user} connected with internet speed {internet_speed} mb/s at time {round(arrival_time, 4)}")
        
        # Begin Customer cycle

        # Get help desk
        if random.choice([True, False]):
            print("Called help desk")
            env.process(call_helpdesk(env, user, cloud)) # Request help desk
            
        # Access site
        print("Accessed site")
        env.process(open_website(env, user, cloud, internet_speed)) # Request website

        # End Customer cycle
        
        yield env.timeout(random.randint(10, 50)/60) # Randomized interarrival times
        


def get_avg_wait_time(wait_times):
    avg_wait = statistics.mean(wait_times)
    # Calculate time
    minutes, frac_minutes = divmod(avg_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)

# Get user input
def user_input():
    num_of_nodes = input("Input # number of nodes: ")
    num_of_helpdesks = input("Input # number of desk employees: ")
    params = [num_of_nodes, num_of_helpdesks]
    if(all(str(i).isdigit for i in params)):
        params = [int(x) for x in params]
    else:
        print("Enter valid integer number, Simulation will use default node=1 helpdesks=1")
        params = [1,1]
    return params

def main():
    num_of_nodes, num_of_helpdesks = user_input()

    env = simpy.Environment()
    env.process(run_cloud(env, num_of_nodes, num_of_helpdesks))
    env.run(until=180)

    mins, secs = get_avg_wait_time(wait_times)
    print(f"Running Simulation, the avg wait time is {mins} minutes and {secs} seconds")

main()