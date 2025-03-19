using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Scoring.DTO;
using Scoring.Models;
using Scoring.Utils;
using System.Reflection;

namespace Scoring.Controllers
{
    [Route("api/v1")]
    [ApiController]
    public class UserController : Controller
    {
        private readonly LoggingHelper _logger;
        private readonly IAuthenticationService _authenticationService;

        public UserController(LoggingHelper logger, IAuthenticationService authenticationService)
        {
            _logger = logger;
            _authenticationService = authenticationService;
        }

        [HttpPost("authorization")]
        public ActionResult<UserDTO> AuthenticateUser([FromBody] AuthorizationDTO authorizationData)
        {
            try
            {
                _logger.LogMethodCalled(nameof(AuthenticateUser));

                var user = new User
                {
                    Login = authorizationData.Login,
                    Password = authorizationData.Password
                };

                if (user != null)
                {
                    var userDTO = new UserDTO
                    {
                        UserId = user.UserId ?? 0,
                        Name = user.Name ?? string.Empty,
                        Surname = user.Surname ?? string.Empty,
                        Login = user.Login ?? string.Empty,
                        Password = user.Password ?? string.Empty
                    };

                    return Ok(userDTO);
                }
                else
                {
                    var responseDTO = new ErrorResponseDTO
                    {
                        ErrorCode = 401,
                        ErrorMessage = "Ошибка авторизации"
                    };
                    return Unauthorized(responseDTO);
                }
            }
            catch (Exception ex) 
            {
                _logger.LogError(ex, "Server error: {Message}", ex.Message);
                var responseDTO = new ErrorResponseDTO
                {
                    ErrorCode = 500,
                    ErrorMessage = "Ошибка на стороне сервера"
                };
                return StatusCode(500, responseDTO);
            }
        }
    }
}