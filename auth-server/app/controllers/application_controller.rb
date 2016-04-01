# Main application controller
class ApplicationController < ActionController::Base
  protect_from_forgery with: :null_session

  def success(message)
    render json: { message: message }
  end

  def error(message)
    render json: { error: message }, status: :unprocessable_entity
  end

  def app_sub_uri
    ENV['APP_SUB_URI'].to_s.chomp('/')
  end
end
