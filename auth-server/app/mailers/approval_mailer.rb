# Mailer for user approval confirmations
class ApprovalMailer < ApplicationMailer
  def confirmation(email)
    @email = email

    mail(to: @email,
         subject: "Learning Registry approval confirmation for #{@email}")
  end
end
