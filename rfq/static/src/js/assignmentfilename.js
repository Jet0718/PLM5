// ​ @odoo-module
import { ListRenderer } from "@web/views/list/list_renderer";
import { registry } from "@web/core/registry";


export class CustomListRenderer extends ListRenderer {

  setup() {
    console.log("渲染器已加載"); // 確認執行
    debugger; // 手動觸發斷點
    super.setup();
    // 動態綁定文件選擇事件
    this.useListener('change', 'input[type="file"]', this._onFileInputChange);
  }

  _onFileInputChange(ev) {
    const input = ev.target;
    const fileName = input.files[0]?.name || '';
    const fieldName = input.name === 'file' ? 'file_name' : 'attach_file_name';
    debugger; // 調試信息
    // 定位同行輸入框
    const row = input.closest('tr');
    const targetInput = row.querySelector(`input[name="${fieldName}"]`);
    if (targetInput) {
      targetInput.value = fileName;
      targetInput.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }
}

// 注冊自定義渲染器
registry.category("list_renderers").add("custom_demand_list_renderer", CustomListRenderer);