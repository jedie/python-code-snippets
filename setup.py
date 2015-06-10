    if "publish" in sys.argv:
        try:
            # Test if wheel is installed, otherwise the user will only see:
            #   error: invalid command 'bdist_wheel'
            import wheel
        except ImportError as err:
            print("\nError: %s" % err)
            print("\nMaybe https://pypi.python.org/pypi/wheel is not installed or virtualenv not activated?!?")
            print("e.g.:")
            print("    ~/your/env/$ source bin/activate")
            print("    ~/your/env/$ pip install wheel")
            sys.exit(-1)
     
        if "dev" in __version__:
            print("\nERROR: Version contains 'dev': v%s\n" % __version__)
            sys.exit(-1)
     
        import subprocess
     
        def verbose_check_output(*args):
            print("\nCall: %r\n" %  " ".join(args))
            try:
                return subprocess.check_output(args, universal_newlines=True)
            except subprocess.CalledProcessError as err:
                print("\n***ERROR:")
                print(err.output)
                raise
     
        def verbose_check_call(*args):
            print("\nCall: %r\n" %  " ".join(args))
            subprocess.check_call(args, universal_newlines=True)
     
        # Check if we are on 'master' branch:
        output = verbose_check_output("git", "branch", "--no-color")
        if "* master" in output:
            print("OK")
        else:
            print("\nNOTE: It seems you are not on 'master':")
            print(output)
            if input("\nPublish anyhow? (Y/N)").lower() not in ("y", "j"):
                print("Bye.")
                sys.exit(-1)
     
        # publish only if git repro is clean:
        output = verbose_check_output("git", "status", "--porcelain")
        if output == "":
            print("OK")
        else:
            print("\n***ERROR: git repro not clean:")
            print(output)
            sys.exit(-1)
     
        # tag first (will raise a error of tag already exists)
        verbose_check_call("git", "tag", "v%s" % __version__)
     
        # build and upload to PyPi:
        verbose_check_call(sys.executable or "python", "setup.py", "sdist", "bdist_wheel", "upload")
     
        # push
        verbose_check_call("git", "push")
        verbose_check_call("git", "push", "--tags")
     
        sys.exit(0)