Rails.application.config.middleware.use OmniAuth::Builder do
  provider :google_oauth2, Rails.application.secrets.google_client_id,
           Rails.application.secrets.google_client_secret,
           name: 'google', scope: 'email'

  provider :amazon, Rails.application.secrets.amazon_client_id,
           Rails.application.secrets.amazon_client_secret,
           scope: 'profile'
end
