from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_index = session.get("current_question_index")
    if current_question_index is None:
        session["current_question_index"] = 0
        session["answers"] = {}
        session.save()
        bot_responses.append(BOT_WELCOME_MESSAGE)
        next_question, options = get_next_question(0)
        bot_responses.append(next_question)
        bot_responses.append("\n".join(options))  
    else:
        success, error = record_current_answer(message, current_question_index, session)

        if not success:
            return [error]

        current_question_index += 1

        next_question, options = get_next_question(current_question_index)

        if next_question:
            bot_responses.append(next_question)
            bot_responses.append("\n".join(options))  
        else:
            final_response = generate_final_response(session)
            bot_responses.append(final_response)

        session["current_question_index"] = current_question_index
        session.save()

    return bot_responses


def record_current_answer(answer, current_question_index, session):
    '''
    Validates and stores the answer for the current question to the Django session.
    Returns a tuple (success_flag, error_message).
    '''
    if current_question_index is None or current_question_index < 0 or current_question_index >= len(PYTHON_QUESTION_LIST):
        return False, "No current question to answer."

    question = PYTHON_QUESTION_LIST[current_question_index]
    correct_answer = question.get('answer')

    if correct_answer is None:
        return False, "Current question does not have a valid answer."

    is_correct = (answer.strip().lower() == correct_answer.strip().lower())

    session['answers'][current_question_index] = {
        'answer': answer,
        'is_correct': is_correct
    }
    session.save()
    return True, ""  


def get_next_question(current_question_index):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_index.
    Returns (next_question_text, options).
    '''
    if current_question_index is None or current_question_index < 0 or current_question_index >= len(PYTHON_QUESTION_LIST):
        return None, None

    next_question = PYTHON_QUESTION_LIST[current_question_index]
    return next_question['question_text'], next_question['options']


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    answers = session.get('answers', {})
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = sum(1 for answer in answers.values() if answer['is_correct'])

    result_message = (
        f"You have completed the quiz! \n"
        f"Total questions: {total_questions} \n"
        f"Correct answers: {correct_answers} \n"
        f"Your score: {correct_answers}/{total_questions} \n\n"
    )

    detailed_feedback = "\nDetailed feedback:\n"
    for index, question in enumerate(PYTHON_QUESTION_LIST):
        user_answer = answers.get(index, {}).get('answer', "No answer provided")
        correct_answer = question['answer']
        is_correct = answers.get(index, {}).get('is_correct', False)
        feedback = "Correct" if is_correct else "Incorrect"
        detailed_feedback += (
            f"Question: {question['question_text']} \n"
            f"Options: {', '.join(question['options'])} \n"
            f"Your answer: {user_answer} \n"
            f"Correct answer: {correct_answer} \n"
            f"Result: {feedback} \n\n"
        )

    final_response = result_message + detailed_feedback
    return final_response
