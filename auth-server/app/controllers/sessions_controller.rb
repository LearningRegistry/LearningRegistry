# Controller that gets called after the user has authenticated with a provider
class SessionsController < ApplicationController
  def new
    render text: 'LR AUth Server - Main page'
  end

  def create
    email = auth_hash[:info][:email]

    if User.exists?(email)
      session[:user_id] = email

      render json: session
    else
      redirect_to new_approval_url
    end
  end

  def destroy
    session[:user_id] = nil

    redirect_to verify_url, notice: 'You have been logged out'
  end

  protected

  def auth_hash
    request.env['omniauth.auth'].with_indifferent_access
  end
end
