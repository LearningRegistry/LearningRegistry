# Represents a user in CouchDB
class User < CouchRest::Model::Base
  use_database '_users'

  def self.model_type_value
    'user'
  end

  property :name, String
  property :password, String
  property :roles, [String]
  property :browserid
  property :oauth, Object

  design do
    view :by_name
  end

  def self.exists?(email)
    find_by_name(email) ? true : false
  end

  def self.get_auth_session(email, password)
    response = RestClient.post "#{database.host}/_session",
                               name: email,
                               password: password
    response.cookies['AuthSession']
  rescue RestClient::Unauthorized
    false
  end
end
