# Represents a user in CouchDB
class User < CouchRest::Model::Base
  use_database '_users'

  def self.model_type_value
    'user'
  end

  property :name, String
  property :roles, [String]
  property :browserid
  property :oauth, Object

  design do
    view :by_name
  end

  def self.exists?(email)
    find_by_name(email) ? true : false
  end
end
