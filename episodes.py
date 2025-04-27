import re
from collections import defaultdict

def extract_episodes_from_text(text_data):
    """
    Extract episode information from text data with scene markers.
    
    Args:
        text_data (str): The full text content with scene markers
        
    Returns:
        dict: {episode_code: {'title': str, 'scenes': list}}
        list: All scenes with their episode context
    """
    episodes = defaultdict(dict)
    scenes_with_episodes = []
    current_episode = None
    current_episode_title = None
    
    # Regex to match episode lines (e.g., "1x02 The Bicycle Thief")
    episode_pattern = re.compile(r'(\d+)x(\d+)\s*(.*)')
    
    lines = text_data.split('\n')
    scene_buffer = []
    in_scene = False
    
    for line in lines:
        line = line.strip()
        
        # Detect scene start
        if line.startswith('===') and 'Scene' in line:
            in_scene = True
            scene_buffer = [line]
            continue
            
        # Detect scene end
        if in_scene and line.startswith('---'):
            in_scene = False
            if scene_buffer and current_episode:
                scene_content = '\n'.join(scene_buffer)
                episodes[current_episode]['scenes'].append(scene_content)
                scenes_with_episodes.append({
                    'episode': current_episode,
                    'title': current_episode_title,
                    'scene': scene_content
                })
            continue
            
        # Process scene content
        if in_scene:
            scene_buffer.append(line)
            
            # Check for episode info line (e.g., "1x02 The Bicycle Thief")
            match = episode_pattern.match(line)
            if match:
                season, episode_num, title = match.groups()
                episode_code = f"S{season}E{episode_num.zfill(2)}"
                current_episode = episode_code
                current_episode_title = title.strip()
                
                # Initialize episode if not already present
                if episode_code not in episodes:
                    episodes[episode_code] = {
                        'title': title.strip(),
                        'scenes': []
                    }
    
    return dict(episodes), scenes_with_episodes

def process_scene_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text_data = f.read()
    
    episodes, scenes = extract_episodes_from_text(text_data)
    
    print(f"Found {len(episodes)} episodes:")
    for ep_code, data in episodes.items():
        print(f"{ep_code}: {data['title']} ({len(data['scenes'])} scenes)")
    
    return episodes, scenes

if __name__ == "__main__":
    # Process scene file
    episode_data, scene_data = process_scene_file("modern_family_scenes.txt")
    
    # Save structured data
    import json
    with open("episodes.json", "w") as f:
        json.dump(episode_data, f, indent=2)
    
    print("\nExample scene from first episode:")
    first_ep = next(iter(episode_data.values()))
    if first_ep['scenes']:
        print(first_ep['scenes'][0][:500])  # Print first 500 chars of first scene