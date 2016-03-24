# Helper methods for approval related tests
module ApprovalTestUtils
  def approval_attributes
    {
      organization_name: 'Example Company',
      contact_person: 'John Smith',
      email: 'john@example.org',
      estimated_records: '100',
      sample_record: 'This is my record'
    }
  end

  def valid_token
    JWT.encode(default_payload, secret, 'HS256')
  end

  def expired_token
    expired_payload = default_payload
    expired_payload[:exp] = 1.week.ago.to_i

    JWT.encode(expired_payload, secret, 'HS256')
  end

  def invalid_token
    JWT.encode(default_payload, 'another-secret', 'HS256')
  end

  def default_payload
    {
      email: 'me@example.org',
      action: 'approve',
      exp: 2.weeks.from_now.to_i
    }
  end

  def secret
    Rails.application.secrets.secret_key_base
  end
end
