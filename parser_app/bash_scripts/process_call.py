from subprocess import call


# Create necessary models for a parser operation
def create_models():
    """
    Executing commands: './manage.py makemigrations' and './manage.py migrate'

    """
    try:
        # Make executable the first_launch script (first_launch: makemigrations, migrate)
        call(['chmod', '+x', './parser_app/bash_scripts/first_launch.sh'])
        # Execute first_launch script
        call('parser_app/bash_scripts/first_launch.sh')
    except Exception as e:
        raise e
