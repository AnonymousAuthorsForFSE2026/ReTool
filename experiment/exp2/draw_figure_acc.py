# 堆叠柱状图
import matplotlib.pyplot as plt
import json

def draw_figure(metric, y_min, y_max):
    """
    metric: "testcase precision" / "testcase recall" / "testcase f1" / "scenario precision" / "scenario_recall" / "scenario_f1"
    """
    ours_y_actual = []
    for i in [6,7,11,1,2,9]:
        ours_data = json.load(open(f"log2/ours_result_dataset{i}.json", "r", encoding="utf-8"))
        ours_y_actual.append(ours_data[f"{metric.split(' ')[0]}_reuse_{metric.split(' ')[1]}"])
    for i in range(len(ours_y_actual)):
        ours_y_actual[i] = ours_y_actual[i] * 100

    grok_y_actual = []
    for i in [6,7,11,1,2,9]:
        grok_data = json.load(open(f"log2/grok_result_dataset{i}.json", "r", encoding="utf-8"))
        grok_y_actual.append(grok_data[f"{metric.split(' ')[0]}_reuse_{metric.split(' ')[1]}"])
    for i in range(len(grok_y_actual)):
        grok_y_actual[i] = grok_y_actual[i] * 100

    gpt_y_actual = []
    for i in [6,7,11,1,2,9]:
        gpt_data = json.load(open(f"log2/gpt_result_dataset{i}.json", "r", encoding="utf-8"))
        gpt_y_actual.append(gpt_data[f"{metric.split(' ')[0]}_reuse_{metric.split(' ')[1]}"])
    for i in range(len(gpt_y_actual)):
        gpt_y_actual[i] = gpt_y_actual[i] * 100

    # 开始画图
    plt.figure(figsize=(10, 5))
    bar_width = 0.25
    x = range(1, 7)

    plt.bar([i - bar_width for i in x], grok_y_actual, width=bar_width, label="Grok-4", alpha=0.7, color="#1f77b4")
    plt.bar(x, gpt_y_actual, width=bar_width, label="GPT-5", alpha=0.7, color="#ff7f0e")
    plt.bar([i + bar_width for i in x], ours_y_actual, width=bar_width, label="ReTool", alpha=0.7, color="#2ca02c")
    
    # 写上文字
    for i in x:
        plt.text(i - bar_width, grok_y_actual[i - 1] + 10, f"{grok_y_actual[i - 1]:.1f}", ha='center', va='top', fontsize=25, rotation=0)
        if i == 6 and gpt_y_actual[i-1] > 70:
            plt.text(i, gpt_y_actual[i - 1]- 2, f"{gpt_y_actual[i - 1]:.1f}", ha='center', va='top', fontsize=25, rotation=0)
        else:
            plt.text(i, gpt_y_actual[i - 1] + 10, f"{gpt_y_actual[i - 1]:.1f}", ha='center', va='top', fontsize=25, rotation=0)
        plt.text(i + bar_width, ours_y_actual[i - 1] - 2, f"{ours_y_actual[i - 1]:.1f}", ha='center', va='top', fontsize=25, rotation=0)

    # 堆叠柱状图，上层最大值为100
    plt.bar([i - bar_width for i in x], [100 - h for h in grok_y_actual], width=bar_width, alpha=0.7, bottom=grok_y_actual, color="#d3d3d3")
    plt.bar(x, [100 - h for h in gpt_y_actual], width=bar_width, alpha=0.7, bottom=gpt_y_actual, color="#d3d3d3")
    plt.bar([i + bar_width for i in x], [100 - h for h in ours_y_actual], width=bar_width, alpha=0.7, bottom=ours_y_actual, color="#d3d3d3")

    plt.ylim(y_min, y_max)
    plt.yticks([0, 20, 40, 60, 80, 100], fontsize=25)
    # plt.xlabel("Dataset")
    new_metric = ""
    if metric.split(" ")[0] == "testcase":
        new_metric = "Test Case Reuse " + metric.split(" ")[1][0].upper() + metric.split(" ")[1][1:]
    else:
        new_metric = "Test Suite Reuse " + metric.split(" ")[1][0].upper() + metric.split(" ")[1][1:]
    if "f1" not in metric:
        new_metric += " (%)"
    plt.ylabel(new_metric, fontsize=25)
    plt.xticks(x, [f"{i}" for i in x], fontsize=25)
    plt.xlabel("Dataset", fontsize=25)
    plt.legend(fontsize=23, frameon=True, ncol=3, shadow=True, loc="upper center", borderaxespad=0.1)

    plt.tight_layout()
    metric = metric.replace("scenario", "testsuite")
    plt.savefig(f"fig/exp2_{metric.replace(' ', '_')}.png", dpi=300, bbox_inches='tight')


if __name__ == "__main__":
    draw_figure("testcase precision", 0, 120)
    draw_figure("testcase recall", 0, 120)
    draw_figure("testcase f1", 0, 120)
    draw_figure("scenario precision", 0, 120)
    draw_figure("scenario recall", 0, 120)
    draw_figure("scenario f1", 0, 120)