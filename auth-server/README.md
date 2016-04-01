# Learning Registry - Authentication Sever
The new Learning Registry's authentication server (or auth server for short) is
a small Ruby on Rails 4.2 application that replaces the previous `browserid`
based authentication by using multiple OAuth2/OpenID Connect providers.

Currently it enables authentication from the following services:
* [Google](https://developers.google.com/identity/protocols/OpenIDConnect)
* [Amazon](http://login.amazon.com/)
* [Microsoft Windows Live](https://msdn.microsoft.com/en-us/library/dn631819.aspx)

## System Requirements
The application has been tested and is known to work with Ruby MRI 2.3.x.
However, it should work with other Ruby implementations as well (like JRuby or
Rubinius).

## Configuration

### Auth Server
There are a couple of configuration files that need to be tweaked before
booting up the service:

* `auth-server/config/secrets.yml`: basically application-wide settings
* `auth-server/config/couchdb.yml`: settings related to the connection to the
CouchDB instance

#### Environment variables
The auth server application follows the principles of the
[Twelve-Factor App](http://12factor.net/config), so all configuration settings
that may change between deploys are stored as environment variables.

Overall, for all environments but development & test, you'll need to set the
following environment variables:

* `RAILS_ENV`: the current environment. Can be `development`, `test` or
`production`, among others.
* `SMTP_ADDRESS`: the SMTP host used for sending e-mails (*i.e: smtp.gmail.com*)
* `SMTP_USERNAME`: the username of the SMTP account. Should be a member of the
group that will receive and manage the approvals.
* `SMTP_PASSWORD`: the password of the SMTP account
* `GOOGLE_CLIENT_ID`: the client ID of your Google application
* `GOOGLE_CLIENT_SECRET`: the secret key of your Google application
* `AMAZON_CLIENT_ID`: the client ID of your Amazon application
* `AMAZON_CLIENT_SECRET`: the secret key of your Amazon application
* `WINDOWSLIVE_CLIENT_ID`: the client ID of your Windows Live application
* `WINDOWSLIVE_CLIENT_SECRET`: the secret key of your Windows Live application
* `SECRET_KEY_BASE`: the secret string used by Rails to sign cookies and other
stuff. You can create a new one running `bin/rake secret` from the command-line
* `COUCHDB_MASTER_PASSWORD`: the master password that will be used when a new
user is created in CouchDB after her approval is confirmed
* `COUCH_DB_USERNAME`: the user to connect to the CouchDB instance. Must have
privileges to create & delete users
* `COUCH_DB_PASSWORD`: the password to connect to the CouchDB instance.
* `APP_SUB_URI`: if your application is deployed to a sub-URI, set this
variable with its value; otherwise don't set it.

### OAuth Key Management Application
Inside `couchdb/apps/kanso/oauth-key-management/lib/app.js` there's a single
configuration variable, `authServerBaseUrl`, that needs to point to the auth's
server base URL.

## Running the application

First of all, you need to run the `bin/setup` command in order to set up the
application. This will install the dependencies (using `bundle install`) as well
as clean up some folders.

### In development
Just run the `bin/rails server` command and, if no errors are reported, the
application should be available at `http://localhost:3000`.

### In staging/production
You can use the application server that you prefer. All of them can be setup
using a reverse proxy mechanism via apache or nginx.

Here are some of the most used ones:

* [Unicorn](https://unicorn.bogomips.org/): a fast HTTP server designed for
fast clients, low latency connections.
* [Passenger](https://www.phusionpassenger.com/library/walkthroughs/deploy/ruby/):
can be run in standalone mode or installed as an apache/nginx module, which
makes deployment easier if you also want to serve other Ruby applications at the
same time.
* [Puma](http://puma.io/): highly optimized for performance. Can use workers
(process fork) and/or threads.

## Running the tests
You can execute the test suite using the `bin/rake test` command.
