
Welcome to Nager Public Holiday API's documentation!
==========================================================

.. image:: https://img.shields.io/github/actions/workflow/status/meisnate12/NagerAPI/tests.yml?branch=master&style=plastic
    :target: https://app.travis-ci.com/meisnate12/NagerAPI
    :alt: Build Testing

.. image:: https://img.shields.io/codecov/c/github/meisnate12/NagerAPI?style=plastic
    :target: https://codecov.io/gh/meisnate12/NagerAPI
    :alt: Build Coverage

.. image:: https://codecov.io/gh/meisnate12/NagerAPI/branch/master/graph/badge.svg?token=lmUl0XqFjd
    :target: https://codecov.io/gh/meisnate12/NagerAPI
    :alt: Build Coverage

.. image:: https://img.shields.io/readthedocs/nagerapi?style=plastic
    :target: https://nagerapi.metamanager.wiki
    :alt: Read the Docs

.. image:: https://img.shields.io/github/v/release/meisnate12/NagerAPI?style=plastic
    :target: https://github.com/meisnate12/NagerAPI/releases
    :alt: GitHub release (latest by date)

.. image:: https://img.shields.io/pypi/v/NagerAPI?style=plastic
    :target: https://pypi.org/project/nagerapi/
    :alt: PyPI

.. image:: https://img.shields.io/pypi/dm/nagerapi.svg?style=plastic
    :target: https://pypi.org/project/nagerapi/
    :alt: Downloads

.. image:: https://img.shields.io/github/commits-since/meisnate12/NagerAPI/latest?style=plastic
    :target: https://github.com/meisnate12/NagerAPI/commits/master
    :alt: GitHub commits since latest release (by date) for a branch

.. image:: https://img.shields.io/badge/-Sponsor_or_Donate-blueviolet?style=plastic
    :target: https://github.com/sponsors/meisnate12
    :alt: GitHub Sponsor

Overview
----------------------------------------------------------
Unofficial Python bindings for the `Nager Public Holiday API <https://date.nager.at/Api>`_. The goal is to make interaction with the API as easy as possible.


Installation & Documentation
----------------------------------------------------------

.. code-block:: python

    pip install nagerapi

Documentation_ can be found at Read the Docs.

.. _Documentation: https://nagerapi.metamanager.wiki


Connecting to Nager
==========================================================

Getting a NagerObjectAPI Instance
----------------------------------------------------------

To connect to the `Nager Public Holiday API <https://date.nager.at/Api>`_ you use the :class:`~nagerapi.NagerObjectAPI` object.

.. code-block:: python

    from nagerapi import NagerObjectAPI

    nager = NagerObjectAPI()


.. code-block:: python

    import nagerapi

    nager = nagerapi.NagerObjectAPI()

Usage Examples
==========================================================

Example: List all 2022 US Holidays.

In this one we get the ``US`` :class:`~nagerapi.Country` Object and call ``public_holidays`` from that object.

.. code-block:: python

    from nagerapi import NagerObjectAPI

    nager = NagerObjectAPI()
    country = nager.country("US")

    for holiday in country.public_holidays(2022):
        print(f"{holiday.name} is on {holiday.date.strftime('%Y-%m-%d')}")

Alternatively you can call ``public_holidays`` from the :class:`~nagerapi.NagerObjectAPI` object directly providing the country code.

.. code-block:: python

    from nagerapi import NagerObjectAPI

    nager = NagerObjectAPI()

    for holiday in nager.public_holidays(2022, "US"):
        print(f"{holiday.name} is on {holiday.date.strftime('%Y-%m-%d')}")


Hyperlinks
----------------------------------------------------------

* `Nager API Docs <https://date.nager.at/swagger/index.html>`_

Usage & Contributions
----------------------------------------------------------
* Source is available on the `Github Project Page <https://github.com/meisnate12/NagerAPI>`_.
* Contributors to NagerAPI own their own contributions and may distribute that code under
  the `MIT license <https://github.com/meisnate12/NagerAPI/blob/master/LICENSE.txt>`_.
