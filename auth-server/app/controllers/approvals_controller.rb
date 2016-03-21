# Main controller for approval requests
class ApprovalsController < ApplicationController
  def new
    @approval = ApprovalForm.new
  end

  def create
    @approval = ApprovalForm.new(params[:approval_form])
    @approval.request = request

    if @approval.deliver
      redirect_to new_approval_url,
                  notice: 'Your approval request has been sent successfully'
    else
      render :new
    end
  end
end
