
import pystache, os

ssl_template = '''
ssl_certificate {{ssl_certificate}};
ssl_certificate_key {{ssl_certificate_key}};

server {
    listen   {{port_https}} ssl;
    server_name $hostname localhost;
    
    access_log  {{nginx_logs}}/learningregistry.access.log lr_log_query;

    ssl_protocols SSLv3;
    ssl_session_cache shared:SSL:1m;

    rewrite /(apps/{{id_management}})$ /$1/ redirect;

    location / {
        uwsgi_pass {{uwsgi_app}};
        include learningregistry_cgi/uwsgi_params;
    }

    location ~ /apps/{{id_management}} {
        rewrite /apps/({{id_management}})/$ /{{couchapp_db}}/_design/$1/index.html break;
        rewrite /apps/(.*) /{{couchapp_db}}/_design/$1 break;
        proxy_pass {{couchdb}};
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Ssl on;
    }
    location /apps {
        rewrite /apps/(.*) /{{couchapp_db}}/$1 break;
        proxy_pass {{couchdb}};
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Ssl on;
    }

    location /publish{
         access_log {{nginx_logs}}/learningregistry.access.log lr_log_no_query ;
         uwsgi_pass {{uwsgi_app}};
         include learningregistry_cgi/uwsgi_params;
    }

    location /incoming {
        # For resource_data access don't log the data.
        access_log   {{nginx_logs}}/learningregistry.access.log lr_log_query;

        proxy_pass   {{couchdb}};
        proxy_redirect     off;

        proxy_set_header   Host             $host;
        proxy_set_header   X-Real-IP        $remote_addr;
        proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
        proxy_max_temp_file_size 0;

        client_max_body_size       10m;
        client_body_buffer_size    128k;

        proxy_connect_timeout      90;
        proxy_send_timeout         90;
        proxy_read_timeout         90;

        proxy_buffer_size          4k;
        proxy_buffers              4 32k;
        proxy_busy_buffers_size    64k;
        proxy_temp_file_write_size 64k;
    }

    # various couchdb urls that should be mapped
    location ~ /_(browserid|config|session|utils|oauth|fb|users) {
        proxy_pass {{couchdb}};
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Ssl on;
    }

}
'''


std_template = '''
server {
    listen   {{port_http}} default;
    server_name $hostname localhost;
    
    access_log  {{nginx_logs}}/learningregistry.access.log lr_log_query;

    rewrite /(apps/{{id_management}})$ /$1/ redirect;

    location / {
        uwsgi_pass {{uwsgi_app}};
        include learningregistry_cgi/uwsgi_params;
    }

    location ~ /apps/{{id_management}} {
        rewrite /apps/({{id_management}})/$ /{{couchapp_db}}/_design/$1/index.html break;
        rewrite /apps/(.*) /{{couchapp_db}}/_design/$1 break;
        proxy_pass {{couchdb}};
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Ssl on;
    }

    location /apps {
        rewrite /apps/(.*) /{{couchapp_db}}/$1 break;
        proxy_pass {{couchdb}};
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Ssl on;
    }

    location /publish{
         access_log {{nginx_logs}}/learningregistry.access.log lr_log_no_query ;
         uwsgi_pass {{uwsgi_app}};
         include learningregistry_cgi/uwsgi_params;
    }

    location /incoming {
        # For resource_data access don't log the data.
        access_log   {{nginx_logs}}/learningregistry.access.log lr_log_query;

        proxy_pass   {{couchdb}};
        proxy_redirect     off;

        proxy_set_header   Host             $host;
        proxy_set_header   X-Real-IP        $remote_addr;
        proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
        proxy_max_temp_file_size 0;

        client_max_body_size       10m;
        client_body_buffer_size    128k;

        proxy_connect_timeout      90;
        proxy_send_timeout         90;
        proxy_read_timeout         90;

        proxy_buffer_size          4k;
        proxy_buffers              4 32k;
        proxy_busy_buffers_size    64k;
        proxy_temp_file_write_size 64k;
    }

    # various couchdb urls that should be mapped
    location ~ /_(browserid|config|session|utils|oauth|fb|users) {
        proxy_pass {{couchdb}};
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Ssl on;
    }

}
'''

non_ssl_template = '''
server {
    listen   {{port_http}} default;
    server_name  $hostname localhost;

    access_log  {{nginx_logs}}/learningregistry.access.log lr_log_query;

    location / {
        uwsgi_pass {{uwsgi_app}};
        include learningregistry_cgi/uwsgi_params;

    }

    location /auth {
        rewrite     ^   https://$server_name:8443$request_uri? permanent;

    }

    location /publish{
         #For publish use the default 
         access_log {{nginx_logs}}/learningregistry.access.log lr_log_no_query ;
         uwsgi_pass {{uwsgi_app}};
         include learningregistry_cgi/uwsgi_params;

    }

    location /incoming {
        # For resource_data access don't log the data.
        access_log   {{nginx_logs}}/learningregistry.access.log lr_log_query;

        proxy_pass   {{couchdb}};
        proxy_redirect     off;

        proxy_set_header   Host             $host;
        proxy_set_header   X-Real-IP        $remote_addr;
        proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
        proxy_max_temp_file_size 0;

        client_max_body_size       10m;
        client_body_buffer_size    128k;

        proxy_connect_timeout      90;
        proxy_send_timeout         90;
        proxy_read_timeout         90;

        proxy_buffer_size          4k;
        proxy_buffers              4 32k;
        proxy_busy_buffers_size    64k;
        proxy_temp_file_write_size 64k;
    }
}
'''

def_context = {
        "id_management": "oauth-key-management",
        "couchapp_db": "apps",
        "couchdb": "http://localhost:5984",
        "uwsgi_app": "127.0.0.1:5000",
        "port_https": 443,
        "nginx_logs": "/usr/local/var/log/nginx",
        "port_http": 80,
        "ssl_certificate": "/usr/local/etc/nginx/certs/server.crt",
        "ssl_certificate_key": "/usr/local/etc/nginx/certs/server.key"
    }


def renderSSLTemplate(context):
    
    return pystache.render(ssl_template, context)
 
def renderNonSSLTemplate(context):

    return pystache.render(non_ssl_template, context)   

def renderStdTemplate(context):

    return pystache.render(std_template, context)


def getSSLSiteConfig(cust_context):

    context = def_context.copy()

    if cust_context:
        context.update(cust_context)

    return renderSSLTemplate(context) + renderNonSSLTemplate(context)

def getSiteConfig(cust_context):
    context = def_context.copy()

    if cust_context:
        context.update(cust_context)

    return renderStdTemplate(cust_context)

def checkFileExists(userInput):
    try:
       with open(userInput) as f: pass
    except IOError as e:
       return False
    return True

def checkDirectoryExists(userInput):
    return os.path.isdir(userInput)

def getFirstValidDefaultFromList(items, validate):
    for item in items:
        if validate(item):
            return item
    return items[0]

def getNGINXSiteConfig(setupInfo, ini_config):
    import setup_utils, urlparse

    std_nginx_log = [
        "/var/log/nginx",
        "/usr/local/var/log"
    ]

    std_nginx_cfg = [
        "/etc/nginx",
        "/usr/local/etc/nginx"
    ]

    def_nginx_log = getFirstValidDefaultFromList(std_nginx_log, checkDirectoryExists)
    def_nginx_cfg = getFirstValidDefaultFromList(std_nginx_cfg, checkFileExists)

    context = {
        "id_management": setupInfo["oauth.app.name"],
        "couchapp_db": ini_config.get("app:main", "couchdb.db.apps"),
        "couchdb": ini_config.get("app:main","couchdb.url"),
        "uwsgi_app": ini_config.get("uwsgi", "socket"),
        "port_https": 443,
        "nginx_logs": def_nginx_log,
        "port_http": 80,
        "ssl_certificate": "%s/certs/server.crt" % def_nginx_cfg,
        "ssl_certificate_key": "%s/certs/server.key" % def_nginx_cfg
    }

    node_url = urlparse.urlsplit(setupInfo['nodeUrl'])
    if node_url.scheme == 'http':
        if node_url.port:
            context["port_http"] = node_url.port

        context["port_https"] = None
    elif node_url.scheme == 'https' and node_url.port:
        context["port_https"] = node_url.port
        context["port_http"] = node_url.port - 443 + 80

        context["port_http"] = setup_utils.getInput("Enter the HTTP (non-SSL) port number the node will operate", context["port_http"])
        context["ssl_certificate"] = setup_utils.getInput("Enter the absolute path to your SSL Certificate", context["ssl_certificate"], validateFunc=checkFileExists)
        context["ssl_certificate_key"] = setup_utils.getInput("Enter the absolute path to your SSL Certificate Key", context["ssl_certificate_key"], validateFunc=checkFileExists)

    context["nginx_logs"] = setup_utils.getInput("Enter the absolute path to the NGINX log directory", context["nginx_logs"])

    if context["port_https"]:
        return getSSLSiteConfig(context)
    else:
        return getSiteConfig(context)


'''
server {
    listen   80 default;
    server_name  localhost;

    access_log  /var/log/nginx/learningregistry.access.log lr_log_query;

    location / {
         uwsgi_pass 127.0.0.1:5000;
         include learningregistry_cgi/uwsgi_params;

    }
    location /publish{
         #For publish use the default 
         access_log /var/log/nginx/learningregistry.access.log lr_log_no_query ;
         uwsgi_pass 127.0.0.1:5000;
         include learningregistry_cgi/uwsgi_params;

        }

    location /incoming {
        # For resource_data access don't log the data.
        access_log   /var/log/nginx/learningregistry.access.log lr_log_query;

        proxy_pass   http://127.0.0.1:5984;
        proxy_redirect     off;

        proxy_set_header   Host             $host;
        proxy_set_header   X-Real-IP        $remote_addr;
        proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
        proxy_max_temp_file_size 0;

        client_max_body_size       10m;
        client_body_buffer_size    128k;

        proxy_connect_timeout      90;
        proxy_send_timeout         90;
        proxy_read_timeout         90;

        proxy_buffer_size          4k;
        proxy_buffers              4 32k;
        proxy_busy_buffers_size    64k;
        proxy_temp_file_write_size 64k;
    }

    #error_page  404  /404.html;

    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   html;
    }

    # proxy the PHP scripts to Apache listening on 127.0.0.1:80
    #
    #location ~ \.php$ {
        #proxy_pass   http://127.0.0.1;
    #}

    # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
    #
    #location ~ \.php$ {
        #fastcgi_pass   127.0.0.1:9000;
        #fastcgi_index  index.php;
        #fastcgi_param  SCRIPT_FILENAME  /scripts$fastcgi_script_name;
        #includefastcgi_params;
    #}

    # deny access to .htaccess files, if Apache's document root
    # concurs with nginx's one
    #
    #location ~ /\.ht {
        #deny  all;
    #}
}
'''

if __name__ == "__main__":
    print (getSSLSiteConfig())
