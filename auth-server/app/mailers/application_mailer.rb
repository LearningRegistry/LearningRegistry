# Top level mailer for application
class ApplicationMailer < ActionMailer::Base
  default from: Rails.application.secrets.approval_sender
end
