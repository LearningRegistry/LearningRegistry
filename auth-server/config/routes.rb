Rails.application.routes.draw do
  get '/verify/:provider', to: 'sessions#new'
  get '/auth/:provider/callback', to: 'sessions#create'
  get '/logout', to: 'sessions#destroy'
  get '/sessions/current', to: 'sessions#current'
  get '/sessions/couchdb/new', to: 'sessions#couchdb_new'
  post '/sessions/couchdb/login', to: 'sessions#couchdb_login'

  resources :approvals, only: %i(new create) do
    get :confirm, on: :collection
    get :delete, on: :collection
  end

  root 'main#index'
end
