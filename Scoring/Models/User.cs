using Scoring.DTO;

namespace Scoring.Models
{
    public class User
    {
        public int? UserId { get; set; }
        public string Login { get; set; }
        public string Password { get; set; }
        public string Name { get; set; }
        public string Surname { get; set; }

        public User() { }

        public User(int userId, string login, string password, string name, string surname)
        {
            UserId = userId;
            Login = login;
            Password = password;
            Name = name;
            Surname = surname;
        }

        public User(UserDTO data)
        {
            UserId = data.UserId;
            Login = data.Login;
            Password = data.Password;
            Name = data.Name;
            Surname = data.Surname;
        }
    }
}
