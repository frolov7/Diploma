using Microsoft.Extensions.Logging;
using System;

namespace Scoring.Utils
{
    public class LoggingHelper
    {
        private readonly ILogger<LoggingHelper> _logger;

        public LoggingHelper(ILogger<LoggingHelper> logger)
        {
            _logger = logger;
        }

        /// <summary>
        /// Логирует, что вызван метод с указанным именем
        /// </summary>
        /// <param name="methodName">Имя метода (например, nameof(AuthenticateUser))</param>
        public void LogMethodCalled(string methodName)
        {
            _logger.LogInformation("Вызван метод: {MethodName}", methodName);
        }

        /// <summary>
        /// Логирует ошибку с деталями исключения
        /// </summary>
        /// <param name="ex">Исключение</param>
        /// <param name="description">Описание контекста или действия</param>
        /// <param name="methodName">Имя метода, где возникла ошибка (например, nameof(AuthenticateUser))</param>
        public void LogError(Exception ex, string description, string methodName)
        {
            _logger.LogError(ex, "Ошибка в методе {MethodName}. Описание: {Description}", methodName, description);
        }

        /// <summary>
        /// Логирует отладочное сообщение
        /// </summary>
        /// <param name="message">Сообщение</param>
        /// <param name="methodName">Имя метода (например, nameof(AuthenticateUser))</param>
        public void LogDebug(string message, string methodName)
        {
            _logger.LogDebug("Отладка в методе {MethodName}: {Message}", methodName, message);
        }
    }
}
