# Controller that gets called after the user has authenticated with a provider
class SessionsController < ApplicationController
  def new
    render text: 'LR AUth Server - Main page'
  end

  def create
    check_params; return if performed?

    email = auth_hash[:info][:email]

    if User.exists?(email)
      session[:user_id] = email

      redirect_to omniauth_params[:back_url]
    else
      redirect_to new_approval_url
    end
  end

  def destroy
    session[:user_id] = nil

    redirect_to verify_url, notice: 'You have been logged out'
  end

  def current
    if session[:user_id].present?
      render json: { email: session[:user_id] }
    else
      head :unauthorized
    end
  end

  protected

  def check_params
    if omniauth_params[:back_url].blank?
      response = { error: 'back url is missing' }

      render json: response, status: :bad_request and return
    end
  end

  def auth_hash
    request.env['omniauth.auth'].with_indifferent_access
  end

  def omniauth_params
    request.env['omniauth.params'].with_indifferent_access
  end
end
