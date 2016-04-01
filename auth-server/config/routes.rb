Rails.application.routes.draw do
  get '/verify/:provider', to: 'sessions#new'
  get '/auth/:provider/callback', to: 'sessions#create'
  get '/logout', to: 'sessions#destroy'
  get '/sessions/current', to: 'sessions#current'

  resources :approvals, only: %i(new create) do
    get :confirm, on: :collection
    get :delete, on: :collection
  end

  root 'main#index'
end
