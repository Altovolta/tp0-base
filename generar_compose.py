import sys
import yaml

def add_server_compose(compose_config):
    server_compose = {
                        'container_name': 'server',  
                        'image': 'server:latest',
                        'entrypoint': 'python3 /main.py',
                        'environment': ['PYTHONUNBUFFERED=1', 'LOGGING_LEVEL=DEBUG'],
                        'networks': ['testing_net']
                     }
    
    compose_config['services']['server'] = server_compose

def add_client_compose(compose_config, client_id):
    client_name = f"client{client_id}"
    client_compose = {
                        'container_name': client_name,
                        'image': 'client:latest',
                        'entrypoint': '/client',
                        'environment': [f'CLI_ID={client_id}', 'CLI_LOG_LEVEL=DEBUG'],
                        'networks': ['testing_net'],
                        'depends_on': ['server']
                        }
    
    compose_config['services'][client_name] = client_compose

def add_network_compose(compose_config):
    network_compose = {
                        'testing_net': {
                            'ipam': {
                                'driver': 'default',
                                'config': [ {'subnet': '172.25.125.0/24'} ]
                            }
                        }
                    }
    
    compose_config['networks'] = network_compose
    
def main():
    argv = sys.argv
    file_name = argv[1]
    number_of_clients = int(argv[2])

    compose_config = {'name': 'tp0', "services": {}}

    add_server_compose(compose_config)

    for i in range(1, number_of_clients+1):
        add_client_compose(compose_config, i)

    add_network_compose(compose_config)

    with open(file_name, 'w') as file:
        yaml.dump(compose_config, file, sort_keys=False)


main()