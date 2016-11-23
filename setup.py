from setuptools import setup

setup(name='oanda_fx_api',
      version=0.1,
      description='a wrapper for the Oanda fxTrade REST v20 API',
      url='https://github.com/abberger1/fx_algo',
      author='Andrew Berger',
      packages=['oanda_fx_api', 'oanda_fx_api.logic', 'oanda_fx_api.charting', 'oanda_fx_api.tools'],
      install_requires=[x for x in open('requirements.txt', 'r')],
      zip_safe=False)
