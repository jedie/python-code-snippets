import subprocess

def iter_subprocess_output(*popenargs, **kwargs):
    """
    A subprocess with tee ;)
    """
    print("Call: %s" % " ".join(popenargs))

    env = dict(os.environ)
    env["PYTHONUNBUFFERED"]="1" # If a python script called ;)

    proc=subprocess.Popen(popenargs,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        bufsize=1, env=env, universal_newlines=True,
        **kwargs
    )
    return iter(proc.stdout.readline,'')
