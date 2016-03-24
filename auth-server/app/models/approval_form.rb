# Class that represents an approval form and takes care of the sending
class ApprovalForm < MailForm::Base
  attribute :organization_name, validate: true
  attribute :contact_person, validate: true
  attribute :email, validate: /\A([\w\.%\+\-]+)@([\w\-]+\.)+([\w]{2,})\z/i
  attribute :estimated_records, validate: true
  attribute :sample_record, validate: true
  attribute :approval_link
  attribute :delete_link
  attribute :phone, captcha: true

  append :remote_ip, :user_agent

  # Declare the e-mail headers. It accepts anything the mail method
  # in ActionMailer accepts.
  def headers
    {
      subject: '[Learning Registry] New User Approval Request',
      to: Rails.application.secrets.approval_receiver,
      from: Rails.application.secrets.approval_sender
    }
  end
end
