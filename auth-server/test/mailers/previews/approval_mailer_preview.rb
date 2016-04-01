# Preview all emails at http://localhost:3000/rails/mailers/approval_mailer
class ApprovalMailerPreview < ActionMailer::Preview
  def confirmation_preview
    ApprovalMailer.confirmation('john@example.org')
  end
end
