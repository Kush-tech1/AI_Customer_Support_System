import json
import time
from pathlib import Path

from app.graph.workflow import support_graph


DATASET_PATH = Path(__file__).parent / "dataset.json"


def load_dataset():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def check_answer(answer: str, expected_phrases: list[str]) -> bool:
    answer = answer.lower()

    return all(
        phrase.lower() in answer
        for phrase in expected_phrases
    )


def run_evals():

    dataset = load_dataset()[:5]

    intent_correct = 0
    complexity_correct = 0
    order_id_correct = 0
    answer_correct = 0

    print("\n================ EVALUATION RESULTS ================\n")

    for case in dataset:

        result = support_graph.invoke({
            "message": case["message"]
        })

        triage = result["triage"]
        response = result["response"]

        intent_ok = (
            triage["intent"]
            == case["expected_intent"]
        )

        complexity_ok = (
            triage["complexity"]
            == case["expected_complexity"]
        )

        order_id_ok = (
            triage["order_id"]
            == case["expected_order_id"]
        )

        answer_ok = check_answer(
            response["answer"],
            case["expected_answer_contains"],
        )

        if intent_ok:
            intent_correct += 1

        if complexity_ok:
            complexity_correct += 1

        if order_id_ok:
            order_id_correct += 1

        if answer_ok:
            answer_correct += 1

        passed = (
            intent_ok
            and complexity_ok
            and order_id_ok
            and answer_ok
        )

        status = "PASS" if passed else "FAIL"

        print(f"{status}  {case['name']}")

        time.sleep(4)

        if not passed:
            print(f"       Expected intent: {case['expected_intent']}")
            print(f"       Actual intent:   {triage['intent']}")
            print(f"       Expected route:  {case['expected_complexity']}")
            print(f"       Actual route:    {triage['complexity']}")
            print(f"       Answer:          {response['answer']}")

    total = len(dataset)

    print("\n=====================================================")

    print(
        f"Intent accuracy:      "
        f"{intent_correct / total:.1%}"
    )

    print(
        f"Routing accuracy:     "
        f"{complexity_correct / total:.1%}"
    )

    print(
        f"Order ID accuracy:    "
        f"{order_id_correct / total:.1%}"
    )

    print(
        f"Answer checks:        "
        f"{answer_correct / total:.1%}"
    )

    print("=====================================================\n")


if __name__ == "__main__":
    run_evals()