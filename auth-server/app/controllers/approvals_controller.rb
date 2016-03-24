# Main controller for approval requests
class ApprovalsController < ApplicationController
  before_action :set_approval_values, only: :create
  before_action :set_decoded_token, only: %i(confirm delete)

  def new
    @approval = ApprovalForm.new
  end

  def create
    if @approval.deliver
      redirect_to new_approval_url,
                  notice: 'Your approval request has been sent successfully'
    else
      render :new
    end
  end

  def confirm
    error('Signature validation failed') && return unless @decoded_token.valid?
    error('Approval has already expired') && return if @decoded_token.expired?

    if User.create(user_attributes)
      head :ok
    else
      error('User could not be created')
    end
  end

  def delete
    if @decoded_token.valid?
      User.find_by_name(@decoded_token.email).destroy

      head :ok
    else
      error('Signature validation failed')
    end
  end

  private

  def set_approval_values
    @approval = ApprovalForm.new(params[:approval_form])
    @approval.request = request
    @approval.approval_link = confirm_approvals_url(
      token: approval_process.generate_approval_token
    )
    @approval.delete_link = delete_approvals_url(
      token: approval_process.generate_delete_token
    )
  end

  def set_decoded_token
    @decoded_token = DecodedToken.new(params[:token])
  end

  def approval_process
    @approval_process ||= ApprovalProcess.new(@approval)
  end

  def user_attributes
    {
      id: "org.couchdb.user:#{@decoded_token.email}",
      name: @decoded_token.email,
      oauth: { consumer_keys: { @decoded_token.email => SecureRandom.hex },
               tokens: { node_sign_token: SecureRandom.hex } }
    }
  end
end
