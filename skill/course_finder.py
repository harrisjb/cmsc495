# -*- coding: utf-8 -*-
#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License
# is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
#

# This is a simple Hello World Alexa Skill, built using
# the implementation of handler classes approach in skill builder.
import json
import boto3
from pprint import pprint
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import SimpleCard

sb = SkillBuilder()
dynamodb = boto3.resource('dynamodb')
client = boto3.client('dynamodb')
table = dynamodb.Table('courses')

class LaunchRequestHandler(AbstractRequestHandler):
    # Handler for Skill Launch
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech_text = "Welcome to the  \
        <say-as interpret-as='spell-out'>UMUC</say-as> Course Finder,\
        I can help you find \
        available classes for upcoming sessions!<break time='0.5s'/> Say 'ask \
        <say-as interpret-as='spell-out'>UMUC</say-as> Course Finder what \
        semesters are available, or, ask\
        <say-as interpret-as='spell-out'>UMUC</say-as> Course Finder\
        to find MATH classes"

        card_text = "Ask UMUC Course Finder 'What sessions do you have available?'\
        or 'Ask UMUC Course Finder  'Find MATH Classes for Fall 2018 Online Session 1'"
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("UMUC Course Finder", card_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class AvailableSessionsIntentHandler(AbstractRequestHandler):
    # Handler for Hello World Intent
    def can_handle(self, handler_input):
        return is_intent_name("AvailableSessions")(handler_input)

    def handle(self, handler_input):
        response = table.scan()
        classes = response['Items']
        sessions = ["Fall 2018 Online Session 1", "Fall 2018 Online Session 2",
                "Fall 2018 Online Session 3", "Fall 2018 Online Session 4"]

        speech_text = ""
        named_sessions = []

        for c in classes:
          session_name = " " + c['subj'] + " " + c['num'] + ", "
          if session_name not in named_sessions:
            named_sessions.append(session_name)
            #speech_text += class_name

        session_count = str(len(sessions))
        speech_text += "I have " + session_count + " sessions available: "

        for s in sessions:
            speech_text += " " + s + " ,"

        speech_text += " If you want to know about classes are available \
        for a particular session, say 'what classes are available for fall 2018 online session 1'"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Available Sessions", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response

class ClassSectionsIntentHandler(AbstractRequestHandler):
    # Handler for Hello World Intent
    def can_handle(self, handler_input):
        return is_intent_name("ClassSections")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        response = table.scan()
        classes = response['Items']
        classNum = slots.get('classNum')
        named_classes = []

        if classNum.value is None:
          speech_text = "What class details are you interested in?\
                  For example, <say-as interpret-as='spell-out'>CMSC495</say-as>"
        else:
          speech_text = ""

          for c in classes:
            unsan_class_name = " " + c['subj'] + " " + c['num']
            class_name = unsan_class_name.lower().strip()
            class_with_code = classNum.value.lower().strip()
            if class_name == class_with_code:
              named_classes.append(class_name)

          classes_count = str(len(named_classes))
          speech_text = "I have " + str(len(named_classes)) + " sections of "\
           " <say-as interpret-as='spell-out'>" +  classNum.value + \
           "</say-as> classes available. Do you want me to send you enrollment information " \
           + " for the available sections of <say-as interpret-as='spell-out'>"\
           + classNum.value + "</say-as>?"

        handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Class Sections", str(class_with_code))).set_should_end_session(
          False)

        return handler_input.response_builder.response


class ClassDetailIntentHandler(AbstractRequestHandler):
    # Handler for Hello World Intent
    def can_handle(self, handler_input):
        return is_intent_name("ClassDetails")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        response = table.scan()
        classes = response['Items']
        classNum = slots.get('classNum')
        named_classes = []

        if classNum.value is None:

          speech_text = "What class details are you interested in?\
                  For example, <say-as interpret-as='spell-out'>CMSC495</say-as>"
        else:
          speech_text = ""

          for c in classes:

            unsan_class_name = " " + c['subj'] + " " + c['num']
            class_name = unsan_class_name.lower().strip()
            class_with_code = classNum.value.lower().strip()
            if class_name == class_with_code:
              named_classes.append(class_name)
              speech_text += "<say-as interpret-as='spell-out'>" + \
                      class_with_code + "</say-as>" + c['title'] + " Description: " \
                      + c['description'] + " Prerequisites are: " + c['prereq']


        handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Class Details", str(speech_text))).set_should_end_session(
          False)

        return handler_input.response_builder.response


class AvailableClassesIntentHandler(AbstractRequestHandler):
    # Handler for Hello World Intent
    def can_handle(self, handler_input):
        return is_intent_name("AvailableClasses")(handler_input)

    def handle(self, handler_input):
        classes = ["MATH 141", "MATH 115",
                "MATH 142"]

        #type(handler_input.request_envelope.request.intent)
        #class 'ask_sdk_model.intent.Intent'

        slots = handler_input.request_envelope.request.intent.slots
        #pprint(slots)

        #type(slots.get('classCode'))
        #class 'ask_sdk_model.slot.Slot'

        response = table.scan()
        classes = response['Items']
        classCode = slots.get('classCode')
        #classCode = {"value": "CMSC"}
        #dynamodb = DynamoDbAdapter.new(table_name="courses")
        #pprint("dynamo " + str(dynamodb))
        #pprint(type(dynamodb))
        #pprint(relevant_classes)
        #pprint("classCode val: " + str(classCode.value))

        named_classes = []
        if classCode.value is None:
          speech_text = "What 4 letter class code are you interested in? For example, M-A-T-H"

          speech_text = "What 4 letter class code are you interested in?\
                  For example, ask <say-as interpret-as='spell-out'>UMUC</say-as>" \
                  + " Course Finder what <say-as interpret-as='spell-out'>CMSC</say-as>" \
                  + " classes are available for Fall 2018 Online Session 1"
        else:
          speech_text = ""

          for c in classes:
            unsan_class_name = " " + c['subj']
            class_name = unsan_class_name.lower().strip()
            class_with_code = classCode.value.lower().strip()
            if class_name == class_with_code and class_name + " " + c['num'] not in named_classes:
              named_classes.append(class_name + " " + c['num'])

        classes_count = str(len(named_classes))
        speech_text = "I have " + classes_count + \
         " <say-as interpret-as='spell-out'>" + classCode.value + "</say-as> " \
         + " classes available: " + str(named_classes)

        handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Available Classes", str(named_classes))).set_should_end_session(
          False)

        return handler_input.response_builder.response

class EnrollmentInfoIntentHandler(AbstractRequestHandler):
    # Handler for Hello World Intent
    def can_handle(self, handler_input):
        return is_intent_name("EnrollmentInfo")(handler_input)

    def handle(self, handler_input):
        sessions = ["Fall 2018 Online Session 1", "Fall 2018 Online Session 2",
                "Fall 2018 Online Session 3", "Fall 2018 Online Session 4"]
        session_count = str(len(sessions))
        speech_text = "I have " + session_count + " sessions available: "
        for s in sessions:
            speech_text += " " + s + " ,"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Enrollment Info", speech_text)).set_should_end_session(
            True)
        return handler_input.response_builder.response

class HelpIntentHandler(AbstractRequestHandler):
    # Handler for Help Intent
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "You can ask 'What sessions do you have available' or \
                'Find MATH classes in Fall 2018 Online Session 1'!"

        handler_input.response_builder.speak(speech_text).ask(
            speech_text).set_card(SimpleCard(
                "UMUC Course Finder", speech_text))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    # Single handler for Cancel and Stop Intent
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("UMUC Course Finder", speech_text))
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    # AMAZON.FallbackIntent is only available in en-US locale.
    # This handler will not be triggered except in that locale,
    # so it is safe to deploy on any locale
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = ("The <say-as interpret-as='spell-out'>UMUC</say-as> Course Finder\
            skill can't help you with that. <break time='0.5s'/>"
            "You can ask 'What sessions do you have available', or, \
                'Find MATH classes in Fall 2018 Online Session 1'!")
        reprompt = "You can ask 'What sessions do you have available', or, \
                'Find MATH classes in Fall 2018 Online Session 1'!"

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    # Handler for Session End
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    # Catch all exception handler, log exception and
    # respond with custom message
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        print("Encountered following exception: {}".format(exception))

        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AvailableSessionsIntentHandler())
sb.add_request_handler(AvailableClassesIntentHandler())
sb.add_request_handler(ClassDetailIntentHandler())
sb.add_request_handler(ClassSectionsIntentHandler())
sb.add_request_handler(EnrollmentInfoIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()
