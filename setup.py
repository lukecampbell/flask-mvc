try:
    from setuptools import setup, find_packages
    packages = find_packages()
except ImportError:
    from distutils import setup
    packages = ['flask_mvc','flask_mvc/utils']

setup(name = 'Flask-MVC',
        version='0.0.3',
        description='A framework to extend Flask to follow the model view controller, MVC, web application development pattern.',
        long_description=open('README.md','r').read(),
        license='LICENSE.txt',
        author='Luke Campbell',
        author_email='luke.s.campbell@gmail.com',
        packages=packages,
        package_data={'flask_mvc.utils':['templates/*json']},
        install_requires=['flask==0.9','requests==1.2.0','python-cjson==1.0.5', 'pyyaml==3.10'],
        entry_points={
            'console_scripts':[
                'flask-mvc-generate = flask_mvc.utils.generate:main',
                ],
            }
        )





