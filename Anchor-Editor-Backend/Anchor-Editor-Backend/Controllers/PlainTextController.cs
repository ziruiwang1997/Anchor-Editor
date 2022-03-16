using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Text.RegularExpressions;
using Anchor_Editor_Backend.Repository;
using Anchor_Editor_Backend.Services;
using Anchor_Editor_Backend.Models;

namespace Anchor_Editor_Backend.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class PlainTextController : ControllerBase
    {
        private IXmlRepository _xmlRepository;

        private IXmlDeserializationService _xmlDeserializationService;

        private IAnchorRepository _anchorRepository;

        public PlainTextController(IAnchorRepository anchorRepository, IXmlRepository xmlRepository, IXmlDeserializationService xmlDeserializationService)
        {
            _anchorRepository = anchorRepository;
            _xmlRepository = xmlRepository;
            _xmlDeserializationService = xmlDeserializationService;
        }

        [HttpGet]
        public IActionResult GetPlainTextAsString()
        {
            var originalXmlFile = _xmlRepository.OriginalXmlFile;
            string plainText = _xmlDeserializationService.GetPlainTextAsStringFromXml(originalXmlFile);
            return Ok(plainText);
        }
    }
}
