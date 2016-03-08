# Controller that gets called after the user has authenticated with a provider
class SessionsController < ApplicationController
  def create
    render json: auth_hash
  end

  protected

  def auth_hash
    request.env['omniauth.auth']
  end
end
