# Be sure to restart your server when you modify this file.

Rails.application.config.session_store :cookie_store,
                                       key: '_auth-server_session',
                                       expire_after: 10.minutes
