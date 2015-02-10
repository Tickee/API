from fabric.api import run, sudo, abort, local, settings, env, cd
import datetime

# --- Server configuration ---

def staging():
    env.hosts = ['tickee-api']
    env.user = 'tickee'
    env.is_staging = True
    env.supervisor_worker = 'gunicorn_staging'
    env.code_dir = "/home/tickee/staging"
    
def production():
    env.hosts = ['tickee-api']
    env.user = 'tickee'
    env.is_staging = False
    env.supervisor_worker = 'gunicorn_production'
    env.code_dir = "/home/tickee/deploy"

# --- Mission Control ---

def deploy():
    """Deploying updates to api"""
    test()
    if not env.is_staging:
        backup()
    prepare()
    restart_api()

def to_standby():
    """Directs all requests to the standby server"""
    if env.is_staging:
        print "Redirecting to STANDBY is only allowed for PRODUCTION!"
        return
    with cd(env.code_dir):
        run('ln -sf celeryconfig-gostandby.py ./api/celeryconfig.py')
    restart_api()

def to_main():
    """Directs all requests to the main server"""
    if env.is_staging:
        print "Reverting back to PRODUCTION is not allowed for STAGING!"
        return
    with cd(env.code_dir):
        run('ln -sf celeryconfig-production.py ./api/celeryconfig.py')
    restart_api()
        
# --- Backup ---

def backup():
    today = datetime.datetime.today().strftime('%d-%m-%Y_%H%M%S')
    with cd(env.code_dir):
        run('cp -r . ~/archive/%s' % today)

# --- Deployment ---

def prepare():
    """update to latest version"""
    with cd(env.code_dir):
        run('svn up api')
        run('svn up pyramid-oauth2')

# --- Supervisord ---

def restart_api():
    run("source ~/venvs/api/bin/activate && supervisorctl reread")
    run("source ~/venvs/api/bin/activate && supervisorctl restart %s" % env.supervisor_worker)

# --- Local ---

def test():
    """run test suite"""