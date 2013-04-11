try:
    from setuptools import setup, find_packages
    packages = find_packages()
except ImportError:
    from distutils import setup
    packages = ['flask_mvc']

setup(name = 'Flask-MVC',
        version='0.0.2',
        description='A framework to extend Flask to follow the model view controller, MVC, web application development pattern.',
        long_description=open('README.md','r').read(),
        license='LICENSE.txt',
        author='Luke Campbell',
        author_email='luke.s.campbell@gmail.com',
        packages=packages,
        install_requires=['flask==0.9','requests==1.2.0','python-cjson==1.0.5'],
        )





