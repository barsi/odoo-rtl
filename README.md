# Odoo RTL (Right to left) Project

## For Version 12.0+, Odoo added support for RTL, please refere to offecial [Odoo Installation](https://www.odoo.com/documentation/12.0/setup/install.html) to learn how to enable RTL.

**version 11.0 community**

This project developed as a set of modules to provide Right to left support for Odoo v11.0 community edition (formely known as OpenERP).

the project contains 3 main modules that cover the three main features in odoo that require RTL support:

* the backend module (web module and its descendants).
* the report module.
* the frontend (website) module and its descendant modules.

## Installation

#### For Backend UI
1. [download](https://github.com/barsi/odoo-rtl/archive/11.0.zip) and extract the modules in addons folder.
2. restart odoo server.
3. go to settings => update modules list.
4. go to settings => language and make sure your target language (e.g. arabic) is Right to left direction.
5. install **Web RTL** module.
6. go to preference and change your language to an RTL language, or restart your browser if you already using the target language.

#### For Reports
1. Install Report RTL.
2. change your language into RTL language.
3. select any report and print it.

#### For Frontend
1. Install Website RTL
2. go to website, and select the target language.


## Contributions and Support
1. you can post an issue (for bugs and new features).
2. create pull request.
3. or by email (if you dont have github account).


### License
This project is licensed under [AGPL v3](http://www.gnu.org/licenses/agpl-3.0.html) (the same as odoo).

