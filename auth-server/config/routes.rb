Rails.application.routes.draw do
  get '/verify', to: 'sessions#new'
  get '/auth/:provider/callback', to: 'sessions#create'
  get '/logout', to: 'sessions#destroy'

  resources :approvals, only: :new

  root 'sessions#new'
end
